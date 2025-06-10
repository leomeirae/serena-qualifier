/**
 * Function to get a message template by name from the WhatsApp Business Management API.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.templateName - The name of the message template to retrieve.
 * @param {string} args.apiVersion - The version of the API to use.
 * @param {string} args.wabaId - The WhatsApp Business Account ID.
 * @returns {Promise<Object>} - The response from the API containing the message template data.
 */
const executeFunction = async ({ templateName, apiVersion, wabaId }) => {
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const url = `https://graph.facebook.com/${apiVersion}/${wabaId}/message_templates?name=${encodeURIComponent(templateName)}`;

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
    console.error('Error getting message template:', error);
    return { error: 'An error occurred while retrieving the message template.' };
  }
};

/**
 * Tool configuration for getting message templates from the WhatsApp Business Management API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_template_by_name',
      description: 'Get a message template by name from the WhatsApp Business Management API.',
      parameters: {
        type: 'object',
        properties: {
          templateName: {
            type: 'string',
            description: 'The name of the message template to retrieve.'
          },
          apiVersion: {
            type: 'string',
            description: 'The version of the API to use.'
          },
          wabaId: {
            type: 'string',
            description: 'The WhatsApp Business Account ID.'
          }
        },
        required: ['templateName', 'apiVersion', 'wabaId']
      }
    }
  }
};

export { apiTool };