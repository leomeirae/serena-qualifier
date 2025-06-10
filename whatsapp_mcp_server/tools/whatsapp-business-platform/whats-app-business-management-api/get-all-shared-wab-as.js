/**
 * Function to get all shared WhatsApp Business Accounts (WABAs).
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.businessAccountId - The ID of the business account.
 * @param {string} args.apiVersion - The version of the API to use.
 * @returns {Promise<Array>} - The list of shared WABAs.
 */
const executeFunction = async ({ businessAccountId, apiVersion }) => {
  const baseUrl = 'https://graph.facebook.com';
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  try {
    // Construct the URL for the request
    const url = `${baseUrl}/${apiVersion}/${businessAccountId}/client_whatsapp_business_accounts`;

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
    console.error('Error getting shared WABAs:', error);
    return { error: 'An error occurred while getting shared WABAs.' };
  }
};

/**
 * Tool configuration for getting all shared WABAs.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_all_shared_wabas',
      description: 'Get all shared WhatsApp Business Accounts (WABAs).',
      parameters: {
        type: 'object',
        properties: {
          businessAccountId: {
            type: 'string',
            description: 'The ID of the business account.'
          },
          apiVersion: {
            type: 'string',
            description: 'The version of the API to use.'
          }
        },
        required: ['businessAccountId', 'apiVersion']
      }
    }
  }
};

export { apiTool };