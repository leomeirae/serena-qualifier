/**
 * Function to create a catalog template in WhatsApp Business Management API.
 *
 * @param {Object} args - Arguments for creating the catalog template.
 * @param {string} args.name - The name of the catalog template.
 * @param {string} args.language - The language of the catalog template.
 * @param {string} args.category - The category of the catalog template.
 * @param {Array} args.components - The components of the catalog template.
 * @returns {Promise<Object>} - The result of the catalog template creation.
 */
const executeFunction = async ({ name, language, category, components }) => {
  const apiVersion = ''; // will be provided by the user
  const wabaId = ''; // will be provided by the user
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const url = `https://graph.facebook.com/${apiVersion}/${wabaId}/message_templates`;

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
    console.error('Error creating catalog template:', error);
    return { error: 'An error occurred while creating the catalog template.' };
  }
};

/**
 * Tool configuration for creating a catalog template in WhatsApp Business Management API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'create_catalog_template',
      description: 'Create a catalog template in WhatsApp Business Management API.',
      parameters: {
        type: 'object',
        properties: {
          name: {
            type: 'string',
            description: 'The name of the catalog template.'
          },
          language: {
            type: 'string',
            description: 'The language of the catalog template.'
          },
          category: {
            type: 'string',
            description: 'The category of the catalog template.'
          },
          components: {
            type: 'array',
            description: 'The components of the catalog template.'
          }
        },
        required: ['name', 'language', 'category', 'components']
      }
    }
  }
};

export { apiTool };