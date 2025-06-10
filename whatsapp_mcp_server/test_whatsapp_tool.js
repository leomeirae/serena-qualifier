import { readFile } from 'fs/promises';
import path from 'path';

async function testWhatsAppTemplates() {
  try {
    console.log('🚀 Testing WhatsApp MCP Tools...');
    
    // Import the get all templates tool
    const toolPath = './tools/whatsapp-business-platform/whats-app-cloud-api/get-all-templates-default-fields.js';
    const toolModule = await import(toolPath);
    
    console.log('✅ Tool loaded successfully');
    console.log('Available functions:', Object.keys(toolModule));
    
    // Test parameters based on our credentials
    const params = {
      version: 'v19.0',
      wabaId: '10978354087768Z0'  // Our WHATSAPP_BUSINESS_ID
    };
    
    console.log('📋 Testing with params:', params);
    
    // Test the tool
    if (toolModule.get_all_templates) {
      console.log('📱 Calling WhatsApp API...');
      const result = await toolModule.get_all_templates(params);
      console.log('📱 WhatsApp API Response:', JSON.stringify(result, null, 2));
    } else {
      console.log('❌ get_all_templates function not found');
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    console.error('Stack:', error.stack);
  }
}

testWhatsAppTemplates(); 