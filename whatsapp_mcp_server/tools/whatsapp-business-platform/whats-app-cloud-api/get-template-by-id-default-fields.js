/**
 * Function to get a WhatsApp message template by its ID.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.templateId - The ID of the message template to retrieve.
 * @param {string} args.version - The API version to use.
 * @returns {Promise<Object>} - The response containing the message template details.
 */
const executeFunction = async ({ templateId, version }) => {
  const baseUrl = 'https://graph.facebook.com';
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  try {
    // Construct the URL for the request
    const url = `${baseUrl}/${version}/${templateId}`;

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
    console.error('Error retrieving message template:', error);
    return { error: 'An error occurred while retrieving the message template.' };
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
      description: 'Retrieve a WhatsApp message template by its ID.',
      parameters: {
        type: 'object',
        properties: {
          templateId: {
            type: 'string',
            description: 'The ID of the message template to retrieve.'
          },
          version: {
            type: 'string',
            description: 'The API version to use.'
          }
        },
        required: ['templateId', 'version']
      }
    }
  }
};

export { apiTool };