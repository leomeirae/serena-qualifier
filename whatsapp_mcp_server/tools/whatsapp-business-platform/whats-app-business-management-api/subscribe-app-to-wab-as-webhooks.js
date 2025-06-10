/**
 * Function to subscribe an app to a WhatsApp Business Account's webhooks.
 *
 * @param {Object} args - Arguments for subscribing the app.
 * @param {string} args.apiVersion - The API version to use.
 * @param {string} args.wabaId - The ID of the WhatsApp Business Account (WABA).
 * @returns {Promise<Object>} - The result of the subscription request.
 */
const executeFunction = async ({ apiVersion, wabaId }) => {
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const url = `https://graph.facebook.com/${apiVersion}/${wabaId}/subscribed_apps`;

  try {
    // Set up headers for the request
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    // Perform the fetch request
    const response = await fetch(url, {
      method: 'POST',
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
    console.error('Error subscribing app to WABA webhooks:', error);
    return { error: 'An error occurred while subscribing the app to WABA webhooks.' };
  }
};

/**
 * Tool configuration for subscribing an app to WABA's webhooks.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'subscribe_app_to_waba_webhooks',
      description: 'Subscribe an app to a WhatsApp Business Account\'s webhooks.',
      parameters: {
        type: 'object',
        properties: {
          apiVersion: {
            type: 'string',
            description: 'The API version to use.'
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