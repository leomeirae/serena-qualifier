<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

function log_error($msg) {
  file_put_contents(__DIR__ . '/proxy_error.log', date('c') . "  " . $msg . "\n", FILE_APPEND);
}

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit();
}

try {
    // Get form data
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);
    
    if (!$data) {
        throw new Exception('Invalid JSON data');
    }
    
    // Kestra webhook endpoint - FIXED URL
    $kestra_url = 'https://kestra.darwinai.com.br/api/v1/executions/webhook/serena.production/1_lead_activation_flow/converse_production_lead';
    
    // Prepare data for Kestra (ensure field names match what the workflow expects)
    $kestra_data = [
        'name' => $data['name'] ?? '',
        'email' => $data['email'] ?? '',
        'whatsapp' => $data['whatsapp'] ?? $data['phone'] ?? '',
        'cidade' => $data['cidade'] ?? $data['city'] ?? '',
        'estado' => $data['estado'] ?? $data['state'] ?? '',
        'account_value' => $data['account_value'] ?? $data['accountValue'] ?? '',
        'client_type' => $data['client_type'] ?? $data['clientType'] ?? 'residencial'
    ];
    
    log_error("Sending data to Kestra: " . json_encode($kestra_data));
    
    // Send to Kestra
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $kestra_url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($kestra_data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json',
        'Accept: application/json'
    ]);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
    
    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $curl_error = curl_error($ch);
    curl_close($ch);
    
    if ($curl_error) {
        throw new Exception("Curl error: " . $curl_error);
    }
    
    if ($http_code >= 200 && $http_code < 300) {
        // Success
        log_error("Success: HTTP $http_code - $response");
        echo json_encode([
            'success' => true,
            'message' => 'Lead enviado com sucesso!',
            'kestra_response' => json_decode($response, true)
        ]);
    } else {
        // Kestra returned an error
        log_error("Kestra error: HTTP $http_code - $response");
        echo json_encode([
            'success' => false,
            'message' => 'Erro ao processar lead. Tente novamente.',
            'error' => "HTTP $http_code"
        ]);
    }
    
} catch (Exception $e) {
    log_error("Exception: " . $e->getMessage());
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Erro interno do servidor',
        'error' => $e->getMessage()
    ]);
}
?>