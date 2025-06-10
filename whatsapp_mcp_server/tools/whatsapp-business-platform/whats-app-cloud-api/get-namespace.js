/**
 * Function to get the message template namespace from the WhatsApp Cloud API.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.version - The API version to use.
 * @param {string} args.wabaId - The WhatsApp Business Account ID.
 * @returns {Promise<Object>} - The response containing the message template namespace.
 */
const executeFunction = async ({ version, wabaId }) => {
  const baseUrl = 'https://graph.facebook.com';
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;

  try {
    // Construct the URL with the provided version and WABA ID
    const url = new URL(`${baseUrl}/${version}/${wabaId}`);
    url.searchParams.append('fields', 'message_template_namespace');

    // Set up headers for the request
    const headers = {
      'Authorization': `Bearer ${token}`
    };

    // Perform the fetch request
    const response = await fetch(url.toString(), {
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
    console.error('Error getting message template namespace:', error);
    return { error: 'An error occurred while getting the message template namespace.' };
  }
};

/**
 * Tool configuration for getting the message template namespace from the WhatsApp Cloud API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_namespace',
      description: 'Get the message template namespace from the WhatsApp Cloud API.',
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