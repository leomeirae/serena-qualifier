/**
 * Function to get all message templates from the WhatsApp Cloud API.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.version - The API version to use.
 * @param {string} args.wabaId - The WhatsApp Business Account ID.
 * @returns {Promise<Object>} - The response containing message templates.
 */
const executeFunction = async ({ version, wabaId }) => {
  const baseUrl = 'https://graph.facebook.com';
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  try {
    // Construct the URL for the request
    const url = `${baseUrl}/${version}/${wabaId}/message_templates`;

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
    console.error('Error getting message templates:', error);
    return { error: 'An error occurred while getting message templates.' };
  }
};

/**
 * Tool configuration for getting message templates from the WhatsApp Cloud API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_all_templates',
      description: 'Get all message templates from the WhatsApp Cloud API.',
      parameters: {
        type: 'object',
        properties: {
          version: {
            type: 'string',
            description: 'The API version to use.'
          },
          wabaId: {
            type: 'string',
            description: 'The WhatsApp Business Account ID.'
          }
        },
        required: ['version', 'wabaId']
      }
    }
  }
};

export { apiTool };