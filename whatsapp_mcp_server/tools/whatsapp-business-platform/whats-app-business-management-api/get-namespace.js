/**
 * Function to get the message template namespace from the WhatsApp Business Management API.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.apiVersion - The API version to use.
 * @param {string} args.wabaId - The WhatsApp Business Account ID.
 * @returns {Promise<Object>} - The response containing the message template namespace.
 */
const executeFunction = async ({ apiVersion, wabaId }) => {
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const baseUrl = `https://graph.facebook.com/${apiVersion}/${wabaId}`;
  
  try {
    // Set up headers for the request
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    // Perform the fetch request
    const response = await fetch(`${baseUrl}?fields=message_template_namespace`, {
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
 * Tool configuration for getting the message template namespace from the WhatsApp Business Management API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_namespace',
      description: 'Get the message template namespace from the WhatsApp Business Management API.',
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