<?php
// api/submit-form.php

// Configurações de CORS
header("Access-Control-Allow-Origin: https://www.saasia.com.br");
header("Access-Control-Allow-Methods: POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
  // Preflight
  http_response_code(204);
  exit;
}

// Função simples de log
function log_error($msg) {
  file_put_contents(__DIR__ . '/proxy_error.log', date('c') . "  " . $msg . "\n", FILE_APPEND);
}

// Lê o corpo da requisição
$raw = file_get_contents('php://input');
if (!$raw) {
  log_error("Nenhum body recebido");
  http_response_code(400);
  echo json_encode(['status'=>'error', 'message'=>'Body vazio']);
  exit;
}

// Faz a requisição para o Apps Script
$appsScriptUrl = 'https://script.google.com/macros/s/AKfycbwr1iJhBnibullGUHRBfqzUIzjohwloARk3TBnHuI7WHzgKTvsNtTL5u2TSk7TjDStX/exec';
$ch = curl_init($appsScriptUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_POSTFIELDS, $raw);
curl_setopt($ch, CURLOPT_TIMEOUT, 30); // Aumentado para 30 segundos
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true); // Seguir redirecionamentos
curl_setopt($ch, CURLOPT_MAXREDIRS, 5); // Máximo de 5 redirecionamentos

// Log para depuração
log_error("Enviando requisição para: " . $appsScriptUrl);
log_error("Dados enviados: " . $raw);

$result = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curlErr  = curl_error($ch);
$effectiveUrl = curl_getinfo($ch, CURLINFO_EFFECTIVE_URL);

// Log para depuração
log_error("Código HTTP: " . $httpCode);
log_error("URL efetiva após redirecionamentos: " . $effectiveUrl);

curl_close($ch);

if ($curlErr) {
  log_error("cURL Error: $curlErr");
  http_response_code(502);
  echo json_encode(['status'=>'error','message'=>"Erro na requisição ao Apps Script: $curlErr"]);
  exit;
}

// Verifica se o Apps Script respondeu com 200 após seguir os redirecionamentos
if ($httpCode !== 200) {
  log_error("Apps Script HTTP $httpCode — resposta: $result");
  log_error("URL final após redirecionamentos: $effectiveUrl");
  http_response_code(502);
  echo json_encode(['status'=>'error','message'=>"Apps Script retornou HTTP $httpCode"]);
  exit;
}

// Tenta decodificar o JSON retornado
$decoded = json_decode($result, true);
if (json_last_error() !== JSON_ERROR_NONE) {
  log_error("JSON inválido do Apps Script: " . json_last_error_msg());
  log_error("URL final após redirecionamentos: $effectiveUrl");
  log_error("Resposta bruta: " . substr($result, 0, 1000) . (strlen($result) > 1000 ? '...' : ''));
  http_response_code(502);
  echo json_encode(['status'=>'error','message'=>'Resposta inválida do Google Apps Script']);
  exit;
}

// Tudo certo: repassa a resposta
header('Content-Type: application/json');
echo json_encode($decoded);
