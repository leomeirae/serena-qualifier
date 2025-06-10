/**
 * Function to get a WhatsApp message template by its ID.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.templateId - The ID of the message template to retrieve.
 * @param {string} args.apiVersion - The version of the API to use.
 * @returns {Promise<Object>} - The response containing the message template details.
 */
const executeFunction = async ({ templateId, apiVersion }) => {
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const url = `https://graph.facebook.com/${apiVersion}/${templateId}`;
  
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
    console.error('Error fetching message template:', error);
    return { error: 'An error occurred while fetching the message template.' };
  }
};

/**
 * Tool configuration for getting a WhatsApp message template by ID.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_template_by_id',
      description: 'Get a WhatsApp message template by its ID.',
      parameters: {
        type: 'object',
        properties: {
          templateId: {
            type: 'string',
            description: 'The ID of the message template to retrieve.'
          },
          apiVersion: {
            type: 'string',
            description: 'The version of the API to use.'
          }
        },
        required: ['templateId', 'apiVersion']
      }
    }
  }
};

export { apiTool };