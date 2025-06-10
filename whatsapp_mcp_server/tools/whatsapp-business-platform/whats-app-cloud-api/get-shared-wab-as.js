/**
 * Function to get shared WhatsApp Business Accounts (WABAs).
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.version - The API version to use.
 * @param {string} args.businessId - The ID of the business to retrieve WABAs for.
 * @returns {Promise<Object>} - The result of the request to get shared WABAs.
 */
const executeFunction = async ({ version, businessId }) => {
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const baseUrl = `https://graph.facebook.com/${version}/${businessId}/client_whatsapp_business_accounts`;

  try {
    // Set up headers for the request
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    // Perform the fetch request
    const response = await fetch(baseUrl, {
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
 * Tool configuration for getting shared WhatsApp Business Accounts (WABAs).
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_shared_wabas',
      description: 'Get shared WhatsApp Business Accounts (WABAs).',
      parameters: {
        type: 'object',
        properties: {
          version: {
            type: 'string',
            description: 'The API version to use.'
          },
          businessId: {
            type: 'string',
            description: 'The ID of the business to retrieve WABAs for.'
          }
        },
        required: ['version', 'businessId']
      }
    }
  }
};

export { apiTool };