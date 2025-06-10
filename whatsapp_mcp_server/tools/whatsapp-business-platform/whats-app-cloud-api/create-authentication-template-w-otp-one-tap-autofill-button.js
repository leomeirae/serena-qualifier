/**
 * Function to create an authentication template with an OTP one-tap autofill button on WhatsApp.
 *
 * @param {Object} args - Arguments for creating the authentication template.
 * @param {string} args.version - The API version to use.
 * @param {string} args.wabaId - The WhatsApp Business Account ID.
 * @param {Object} args.templateData - The data for the authentication template.
 * @returns {Promise<Object>} - The result of the template creation.
 */
const executeFunction = async ({ version, wabaId, templateData }) => {
  const baseUrl = 'https://graph.facebook.com';
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;

  try {
    // Construct the URL for the API request
    const url = `${baseUrl}/${version}/${wabaId}/message_templates`;

    // Set up headers for the request
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    // Perform the fetch request
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(templateData)
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
    console.error('Error creating authentication template:', error);
    return { error: 'An error occurred while creating the authentication template.' };
  }
};

/**
 * Tool configuration for creating an authentication template on WhatsApp.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'create_auth_template',
      description: 'Create an authentication template with an OTP one-tap autofill button on WhatsApp.',
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
          },
          templateData: {
            type: 'object',
            description: 'The data for the authentication template.'
          }
        },
        required: ['version', 'wabaId', 'templateData']
      }
    }
  }
};

export { apiTool };