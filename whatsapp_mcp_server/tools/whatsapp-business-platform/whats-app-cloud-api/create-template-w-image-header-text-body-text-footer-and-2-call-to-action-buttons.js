/**
 * Function to create a message template with an image header, text body, text footer, and call-to-action buttons on WhatsApp.
 *
 * @param {Object} args - Arguments for creating the message template.
 * @param {string} args.name - The name of the message template.
 * @param {string} args.language - The language code for the template.
 * @param {string} args.category - The category of the message template.
 * @param {Array} args.components - The components of the message template.
 * @returns {Promise<Object>} - The result of the template creation.
 */
const executeFunction = async ({ name, language, category, components }) => {
  const url = 'https://graph.facebook.com/{{Version}}/{{WABA-ID}}/message_templates';
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
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
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
 * Tool configuration for creating a message template on WhatsApp.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'create_message_template',
      description: 'Create a message template with an image header, text body, text footer, and call-to-action buttons on WhatsApp.',
      parameters: {
        type: 'object',
        properties: {
          name: {
            type: 'string',
            description: 'The name of the message template.'
          },
          language: {
            type: 'string',
            description: 'The language code for the template.'
          },
          category: {
            type: 'string',
            description: 'The category of the message template.'
          },
          components: {
            type: 'array',
            description: 'The components of the message template.',
            items: {
              type: 'object',
              properties: {
                type: {
                  type: 'string',
                  description: 'The type of the component (e.g., HEADER, BODY, FOOTER, BUTTONS).'
                },
                format: {
                  type: 'string',
                  description: 'The format of the header component (if applicable).'
                },
                text: {
                  type: 'string',
                  description: 'The text content of the component (if applicable).'
                },
                buttons: {
                  type: 'array',
                  description: 'The buttons for the BUTTONS component (if applicable).',
                  items: {
                    type: 'object',
                    properties: {
                      type: {
                        type: 'string',
                        description: 'The type of the button (e.g., PHONE_NUMBER, URL).'
                      },
                      text: {
                        type: 'string',
                        description: 'The display text of the button.'
                      },
                      phone_number: {
                        type: 'string',
                        description: 'The phone number for the PHONE_NUMBER button (if applicable).'
                      },
                      url: {
                        type: 'string',
                        description: 'The URL for the URL button (if applicable).'
                      }
                    }
                  }
                }
              }
            }
          }
        },
        required: ['name', 'language', 'category', 'components']
      }
    }
  }
};

export { apiTool };