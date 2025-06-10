/**
 * Function to get all business phone numbers with filtering from the WhatsApp Business Management API.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.apiVersion - The API version to use.
 * @param {string} args.wabaId - The WhatsApp Business Account ID.
 * @returns {Promise<Object>} - The result of the phone numbers retrieval.
 */
const executeFunction = async ({ apiVersion, wabaId }) => {
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const baseUrl = 'https://graph.facebook.com';
  
  try {
    // Construct the URL with the necessary parameters
    const url = `${baseUrl}/${apiVersion}/${wabaId}/phone_numbers?fields=id,is_official_business_account,display_phone_number,verified_name&filtering=[{'field':'account_mode','operator':'EQUAL','value':'SANDBOX'}]`;

    // Set up headers for the request
    const headers = {
      'Authorization': `Bearer ${token}`
    };

    // Perform the fetch request
    const response = await fetch(url, {
      method: 'GET',
      headers
    });

    // Check if the response was successful
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData);
    }

    // Parse and return the response data
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error retrieving business phone numbers:', error);
    return { error: 'An error occurred while retrieving business phone numbers.' };
  }
};

/**
 * Tool configuration for retrieving business phone numbers from the WhatsApp Business Management API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_business_phone_numbers',
      description: 'Get all business phone numbers with filtering from the WhatsApp Business Management API.',
      parameters: {
        type: 'object',
        properties: {
          apiVersion: {
            type: 'string',
            description: 'The API version to use.'
          },
          wabaId: {
            type: 'string',
            description: 'The WhatsApp Business Account ID.'
          }
        },
        required: ['apiVersion', 'wabaId']
      }
    }
  }
};

export { apiTool };