/**
 * Function to get all apps subscribed to a WhatsApp Business Account's webhooks.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.apiVersion - The API version to use for the request.
 * @param {string} args.wabaId - The ID of the WhatsApp Business Account (WABA).
 * @returns {Promise<Object>} - The result of the request to get subscribed apps.
 */
const executeFunction = async ({ apiVersion, wabaId }) => {
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const baseUrl = 'https://graph.facebook.com';
  
  try {
    // Construct the URL for the request
    const url = `${baseUrl}/${apiVersion}/${wabaId}/subscribed_apps`;

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
    console.error('Error getting subscribed apps:', error);
    return { error: 'An error occurred while getting subscribed apps.' };
  }
};

/**
 * Tool configuration for getting all apps subscribed to a WhatsApp Business Account's webhooks.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_subscribed_apps',
      description: 'Get all apps subscribed to a WhatsApp Business Account\'s webhooks.',
      parameters: {
        type: 'object',
        properties: {
          apiVersion: {
            type: 'string',
            description: 'The API version to use for the request.'
          },
          wabaId: {
            type: 'string',
            description: 'The ID of the WhatsApp Business Account (WABA).'
          }
        },
        required: ['apiVersion', 'wabaId']
      }
    }
  }
};

export { apiTool };