/**
 * Function to get WhatsApp Business Account (WABA) details.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.version - The API version to use.
 * @param {string} args.wabaId - The ID of the WhatsApp Business Account.
 * @returns {Promise<Object>} - The details of the specified WABA.
 */
const executeFunction = async ({ version, wabaId }) => {
  const baseUrl = 'https://graph.facebook.com';
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  try {
    // Construct the URL for the request
    const url = `${baseUrl}/${version}/${wabaId}`;

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
    console.error('Error fetching WABA details:', error);
    return { error: 'An error occurred while fetching WABA details.' };
  }
};

/**
 * Tool configuration for getting WhatsApp Business Account details.
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
          version: {
            type: 'string',
            description: 'The API version to use.'
          },
          wabaId: {
            type: 'string',
            description: 'The ID of the WhatsApp Business Account.'
          }
        },
        required: ['version', 'wabaId']
      }
    }
  }
};

export { apiTool };