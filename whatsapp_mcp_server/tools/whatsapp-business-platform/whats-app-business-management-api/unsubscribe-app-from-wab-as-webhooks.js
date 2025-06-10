/**
 * Function to unsubscribe an app from a WhatsApp Business Account's webhooks.
 *
 * @param {Object} args - Arguments for the unsubscribe request.
 * @param {string} args.apiVersion - The version of the API to use.
 * @param {string} args.wabaId - The ID of the WhatsApp Business Account (WABA).
 * @returns {Promise<Object>} - The result of the unsubscribe request.
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
      method: 'DELETE',
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
    console.error('Error unsubscribing app from WABA webhooks:', error);
    return { error: 'An error occurred while unsubscribing the app from WABA webhooks.' };
  }
};

/**
 * Tool configuration for unsubscribing an app from WABA's webhooks.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'unsubscribe_app_from_waba_webhooks',
      description: 'Unsubscribe an app from a WhatsApp Business Account\'s webhooks.',
      parameters: {
        type: 'object',
        properties: {
          apiVersion: {
            type: 'string',
            description: 'The version of the API to use.'
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