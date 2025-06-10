/**
 * Function to get business account details from the WhatsApp Business Management API.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.apiVersion - The API version to use.
 * @param {string} args.businessAccountId - The ID of the business account to retrieve.
 * @returns {Promise<Object>} - The details of the business account.
 */
const executeFunction = async ({ apiVersion, businessAccountId }) => {
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const url = `https://graph.facebook.com/${apiVersion}/${businessAccountId}?fields=id,name,timezone_id`;

  try {
    // Set up headers for the request
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
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
    console.error('Error retrieving business account details:', error);
    return { error: 'An error occurred while retrieving business account details.' };
  }
};

/**
 * Tool configuration for getting business account details from the WhatsApp Business Management API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_business_account',
      description: 'Get details of a specific business account.',
      parameters: {
        type: 'object',
        properties: {
          apiVersion: {
            type: 'string',
            description: 'The API version to use.'
          },
          businessAccountId: {
            type: 'string',
            description: 'The ID of the business account to retrieve.'
          }
        },
        required: ['apiVersion', 'businessAccountId']
      }
    }
  }
};

export { apiTool };