/**
 * Function to edit a message template in the WhatsApp Business Management API.
 *
 * @param {Object} args - Arguments for editing the template.
 * @param {string} args.templateId - The ID of the template to be edited.
 * @param {string} args.name - The name of the template.
 * @param {Array} args.components - The components of the template.
 * @param {string} [args.language="en_US"] - The language of the template.
 * @param {string} [args.category="MARKETING"] - The category of the template.
 * @returns {Promise<Object>} - The result of the template edit operation.
 */
const executeFunction = async ({ templateId, name, components, language = 'en_US', category = 'MARKETING' }) => {
  const accessToken = ''; // will be provided by the user
  const apiVersion = 'v16.0'; // specify the API version
  const url = `https://graph.facebook.com/${apiVersion}/${templateId}`;
  
  const body = {
    name,
    components,
    language,
    category
  };

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error editing template:', error);
    return { error: 'An error occurred while editing the template.' };
  }
};

/**
 * Tool configuration for editing a message template in the WhatsApp Business Management API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'edit_template',
      description: 'Edit a message template in the WhatsApp Business Management API.',
      parameters: {
        type: 'object',
        properties: {
          templateId: {
            type: 'string',
            description: 'The ID of the template to be edited.'
          },
          name: {
            type: 'string',
            description: 'The name of the template.'
          },
          components: {
            type: 'array',
            description: 'The components of the template.'
          },
          language: {
            type: 'string',
            description: 'The language of the template.'
          },
          category: {
            type: 'string',
            description: 'The category of the template.'
          }
        },
        required: ['templateId', 'name', 'components']
      }
    }
  }
};

export { apiTool };