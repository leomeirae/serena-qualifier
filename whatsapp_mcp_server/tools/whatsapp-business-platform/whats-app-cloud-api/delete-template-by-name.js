/**
 * Function to delete a WhatsApp message template by its name.
 *
 * @param {Object} args - Arguments for the deletion.
 * @param {string} args.templateName - The name of the template to delete.
 * @param {string} args.version - The API version to use.
 * @param {string} args.wabaId - The WhatsApp Business Account ID.
 * @returns {Promise<Object>} - The result of the deletion operation.
 */
const executeFunction = async ({ templateName, version, wabaId }) => {
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const url = `https://graph.facebook.com/${version}/${wabaId}/message_templates?name=${encodeURIComponent(templateName)}`;

  try {
    // Set up headers for the request
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    // Perform the fetch request
    const response = await fetch(url, {
      method: 'DELETE',
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
    console.error('Error deleting template:', error);
    return { error: 'An error occurred while deleting the template.' };
  }
};

/**
 * Tool configuration for deleting a WhatsApp message template.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'delete_template_by_name',
      description: 'Delete a WhatsApp message template by its name.',
      parameters: {
        type: 'object',
        properties: {
          templateName: {
            type: 'string',
            description: 'The name of the template to delete.'
          },
          version: {
            type: 'string',
            description: 'The API version to use.'
          },
          wabaId: {
            type: 'string',
            description: 'The WhatsApp Business Account ID.'
          }
        },
        required: ['templateName', 'version', 'wabaId']
      }
    }
  }
};

export { apiTool };