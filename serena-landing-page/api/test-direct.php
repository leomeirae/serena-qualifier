<?php
// api/test-direct.php
// Este script testa diretamente o Google Apps Script sem passar pelo proxy

// Configurações de CORS
header("Content-Type: text/plain");

// Dados de teste
$testData = [
    'nomeCompleto' => 'Teste Direto',
    'whatsapp' => '(11) 99999-9999',
    'valorContaLuz' => '200',
    'tipoCliente' => 'casa'
];

$jsonData = json_encode($testData);

// URL do Google Apps Script
$appsScriptUrl = 'https://script.google.com/macros/s/AKfycbwr1iJhBnibullGUHRBfqzUIzjohwloARk3TBnHuI7WHzgKTvsNtTL5u2TSk7TjDStX/exec';

// Configurar cURL
$ch = curl_init($appsScriptUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_MAXREDIRS, 5);
curl_setopt($ch, CURLOPT_VERBOSE, true);

// Capturar saída detalhada
$verbose = fopen('php://temp', 'w+');
curl_setopt($ch, CURLOPT_STDERR, $verbose);

// Executar cURL
echo "Enviando requisição para: $appsScriptUrl\n";
echo "Dados: $jsonData\n\n";

$result = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$effectiveUrl = curl_getinfo($ch, CURLINFO_EFFECTIVE_URL);
$curlErr = curl_error($ch);

// Obter informações detalhadas
rewind($verbose);
$verboseLog = stream_get_contents($verbose);

// Exibir resultados
echo "Código HTTP: $httpCode\n";
echo "URL efetiva: $effectiveUrl\n";

if ($curlErr) {
    echo "Erro cURL: $curlErr\n";
} else {
    echo "Resposta:\n$result\n";
}

echo "\nLog detalhado:\n$verboseLog\n";

curl_close($ch);
