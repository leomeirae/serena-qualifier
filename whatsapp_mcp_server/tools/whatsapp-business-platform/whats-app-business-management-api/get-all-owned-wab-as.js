/**
 * Function to get all owned WhatsApp Business Accounts (WABAs).
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.apiVersion - The API version to use for the request.
 * @param {string} args.businessAccountId - The ID of the business account.
 * @returns {Promise<Object>} - The response containing the owned WABAs.
 */
const executeFunction = async ({ apiVersion, businessAccountId }) => {
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const baseUrl = `https://graph.facebook.com/${apiVersion}/${businessAccountId}/owned_whatsapp_business_accounts`;

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
    console.error('Error getting owned WABAs:', error);
    return { error: 'An error occurred while getting owned WABAs.' };
  }
};

/**
 * Tool configuration for getting all owned WhatsApp Business Accounts (WABAs).
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_owned_wabas',
      description: 'Get all owned WhatsApp Business Accounts (WABAs).',
      parameters: {
        type: 'object',
        properties: {
          apiVersion: {
            type: 'string',
            description: 'The API version to use for the request.'
          },
          businessAccountId: {
            type: 'string',
            description: 'The ID of the business account.'
          }
        },
        required: ['apiVersion', 'businessAccountId']
      }
    }
  }
};

export { apiTool };