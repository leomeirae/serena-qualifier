/**
 * Function to create a message template in WhatsApp Cloud API.
 *
 * @param {Object} args - Arguments for creating the message template.
 * @param {string} args.name - The name of the message template.
 * @param {string} args.language - The language code for the message template.
 * @param {string} args.category - The category of the message template.
 * @param {Array} args.components - The components of the message template.
 * @returns {Promise<Object>} - The result of the message template creation.
 */
const executeFunction = async ({ name, language, category, components }) => {
  const version = ''; // will be provided by the user
  const wabaId = ''; // will be provided by the user
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const url = `https://graph.facebook.com/${version}/${wabaId}/message_templates`;

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
 * Tool configuration for creating a message template in WhatsApp Cloud API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'create_message_template',
      description: 'Create a message template in WhatsApp Cloud API.',
      parameters: {
        type: 'object',
        properties: {
          name: {
            type: 'string',
            description: 'The name of the message template.'
          },
          language: {
            type: 'string',
            description: 'The language code for the message template.'
          },
          category: {
            type: 'string',
            description: 'The category of the message template.'
          },
          components: {
            type: 'array',
            description: 'The components of the message template.'
          }
        },
        required: ['name', 'language', 'category', 'components']
      }
    }
  }
};

export { apiTool };