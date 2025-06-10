/**
 * Function to create an authentication template with an OTP one-tap autofill button on WhatsApp.
 *
 * @param {Object} args - Arguments for creating the authentication template.
 * @param {string} args.apiVersion - The API version to use.
 * @param {string} args.wabaId - The WhatsApp Business Account ID.
 * @param {Object} args.templateData - The data for the authentication template.
 * @param {string} args.templateData.name - The name of the authentication template.
 * @param {string} args.templateData.language - The language for the template.
 * @param {string} args.templateData.category - The category of the template.
 * @param {Array} args.templateData.components - The components of the template.
 * @returns {Promise<Object>} - The result of the template creation.
 */
const executeFunction = async ({ apiVersion, wabaId, templateData }) => {
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const url = `https://graph.facebook.com/${apiVersion}/${wabaId}/message_templates`;
  
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(templateData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData);
    }

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
          apiVersion: {
            type: 'string',
            description: 'The API version to use.'
          },
          wabaId: {
            type: 'string',
            description: 'The WhatsApp Business Account ID.'
          },
          templateData: {
            type: 'object',
            properties: {
              name: {
                type: 'string',
                description: 'The name of the authentication template.'
              },
              language: {
                type: 'string',
                description: 'The language for the template.'
              },
              category: {
                type: 'string',
                description: 'The category of the template.'
              },
              components: {
                type: 'array',
                description: 'The components of the template.'
              }
            },
            required: ['name', 'language', 'category', 'components']
          }
        },
        required: ['apiVersion', 'wabaId', 'templateData']
      }
    }
  }
};

export { apiTool };