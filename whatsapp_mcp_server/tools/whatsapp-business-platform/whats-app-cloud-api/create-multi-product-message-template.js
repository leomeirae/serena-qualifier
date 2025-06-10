/**
 * Function to create a multi-product message template on WhatsApp Cloud API.
 *
 * @param {Object} args - Arguments for creating the message template.
 * @param {string} args.name - The name of the message template.
 * @param {string} args.language - The language code for the message template.
 * @param {string} args.category - The category of the message template.
 * @param {Array} args.components - The components of the message template.
 * @returns {Promise<Object>} - The result of the message template creation.
 */
const executeFunction = async ({ name, language, category, components }) => {
  const baseUrl = 'https://graph.facebook.com';
  const version = ''; // will be provided by the user
  const wabaId = ''; // will be provided by the user
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;

  try {
    // Construct the URL for the API request
    const url = `${baseUrl}/${version}/${wabaId}/message_templates`;

    // Set up headers for the request
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    // Prepare the request body
    const body = JSON.stringify({
      name,
      language,
      category,
      components
    });

    // Perform the fetch request
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body
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
 * Tool configuration for creating a multi-product message template on WhatsApp Cloud API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'create_multi_product_message_template',
      description: 'Create a multi-product message template on WhatsApp Cloud API.',
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