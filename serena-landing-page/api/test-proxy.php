<?php
// Teste simples para o proxy PHP
$data = [
    'nomeCompleto' => 'Teste via PHP',
    'whatsapp' => '(11) 99999-9999',
    'valorContaLuz' => '150',
    'tipoCliente' => 'casa'
];

$jsonData = json_encode($data);

$ch = curl_init('http://localhost/api/submit-form.php');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData);
curl_setopt($ch, CURLOPT_TIMEOUT, 10);

$result = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curlErr = curl_error($ch);
curl_close($ch);

echo "Teste do proxy PHP\n";
echo "==================\n";
echo "Dados enviados: " . $jsonData . "\n\n";

if ($curlErr) {
    echo "Erro cURL: " . $curlErr . "\n";
} else {
    echo "Código HTTP: " . $httpCode . "\n";
    echo "Resposta: " . $result . "\n";
}
