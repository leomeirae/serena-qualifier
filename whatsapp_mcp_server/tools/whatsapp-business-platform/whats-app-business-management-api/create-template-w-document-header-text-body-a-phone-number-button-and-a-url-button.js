/**
 * Function to create a message template in WhatsApp Business Management API.
 *
 * @param {Object} args - Arguments for creating the message template.
 * @param {string} args.apiVersion - The API version to use.
 * @param {string} args.wabaId - The WhatsApp Business Account ID.
 * @param {string} args.name - The name of the template.
 * @param {string} args.language - The language of the template.
 * @param {string} args.category - The category of the template.
 * @param {Array} args.components - The components of the template.
 * @returns {Promise<Object>} - The result of the template creation.
 */
const executeFunction = async ({ apiVersion, wabaId, name, language, category, components }) => {
  const url = `https://graph.facebook.com/${apiVersion}/${wabaId}/message_templates`;
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;

  const body = {
    name,
    language,
    category,
    components
  };

  try {
    // Set up headers for the request
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };

    // Perform the fetch request
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(body)
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
    console.error('Error creating message template:', error);
    return { error: 'An error occurred while creating the message template.' };
  }
};

/**
 * Tool configuration for creating a message template in WhatsApp Business Management API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'create_message_template',
      description: 'Create a message template in WhatsApp Business Management API.',
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
          name: {
            type: 'string',
            description: 'The name of the template.'
          },
          language: {
            type: 'string',
            description: 'The language of the template.'
          },
          category: {
            type: 'string',
            description: 'The category of the template.'
          },
          components: {
            type: 'array',
            description: 'The components of the template.',
            items: {
              type: 'object',
              properties: {
                type: {
                  type: 'string',
                  description: 'The type of the component.'
                },
                format: {
                  type: 'string',
                  description: 'The format of the component (if applicable).'
                },
                text: {
                  type: 'string',
                  description: 'The text of the body component (if applicable).'
                },
                buttons: {
                  type: 'array',
                  description: 'The buttons for the template (if applicable).',
                  items: {
                    type: 'object',
                    properties: {
                      type: {
                        type: 'string',
                        description: 'The type of the button.'
                      },
                      text: {
                        type: 'string',
                        description: 'The text of the button.'
                      },
                      phone_number: {
                        type: 'string',
                        description: 'The phone number for phone number buttons (if applicable).'
                      },
                      url: {
                        type: 'string',
                        description: 'The URL for URL buttons (if applicable).'
                      }
                    }
                  }
                }
              }
            }
          }
        },
        required: ['apiVersion', 'wabaId', 'name', 'language', 'category', 'components']
      }
    }
  }
};

export { apiTool };