/**
 * Function to edit a WhatsApp message template.
 *
 * @param {Object} args - Arguments for editing the template.
 * @param {string} args.templateId - The ID of the template to edit.
 * @param {string} args.name - The name of the template.
 * @param {Array} args.components - The components of the template.
 * @param {string} [args.language="en_US"] - The language of the template.
 * @param {string} [args.category="MARKETING"] - The category of the template.
 * @returns {Promise<Object>} - The result of the template edit operation.
 */
const executeFunction = async ({ templateId, name, components, language = 'en_US', category = 'MARKETING' }) => {
  const baseUrl = 'https://graph.facebook.com';
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const version = ''; // will be provided by the user

  try {
    // Construct the URL for the request
    const url = `${baseUrl}/${version}/${templateId}`;

    // Prepare the request body
    const body = JSON.stringify({
      name,
      components,
      language,
      category
    });

    // Set up headers for the request
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };

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
    console.error('Error editing template:', error);
    return { error: 'An error occurred while editing the template.' };
  }
};

/**
 * Tool configuration for editing WhatsApp message templates.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'edit_template',
      description: 'Edit a WhatsApp message template.',
      parameters: {
        type: 'object',
        properties: {
          templateId: {
            type: 'string',
            description: 'The ID of the template to edit.'
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