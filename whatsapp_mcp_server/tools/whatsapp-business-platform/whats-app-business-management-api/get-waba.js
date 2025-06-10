/**
 * Function to get WhatsApp Business Account (WABA) details.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.apiVersion - The API version to use for the request.
 * @param {string} args.wabaId - The ID of the WhatsApp Business Account to retrieve.
 * @returns {Promise<Object>} - The response data containing WABA details.
 */
const executeFunction = async ({ apiVersion, wabaId }) => {
  const baseUrl = 'https://graph.facebook.com';
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  try {
    // Construct the URL for the request
    const url = `${baseUrl}/${apiVersion}/${wabaId}`;

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
    console.error('Error retrieving WABA details:', error);
    return { error: 'An error occurred while retrieving WABA details.' };
  }
};

/**
 * Tool configuration for getting WhatsApp Business Account (WABA) details.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_waba',
      description: 'Get details of a WhatsApp Business Account (WABA).',
      parameters: {
        type: 'object',
        properties: {
          apiVersion: {
            type: 'string',
            description: 'The API version to use for the request.'
          },
          wabaId: {
            type: 'string',
            description: 'The ID of the WhatsApp Business Account to retrieve.'
          }
        },
        required: ['apiVersion', 'wabaId']
      }
    }
  }
};

export { apiTool };