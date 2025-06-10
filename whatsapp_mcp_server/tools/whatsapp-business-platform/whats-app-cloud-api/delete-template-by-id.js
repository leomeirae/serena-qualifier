/**
 * Function to delete a message template by its ID on WhatsApp Cloud API.
 *
 * @param {Object} args - Arguments for the deletion.
 * @param {string} args.hsm_id - The ID of the template to delete.
 * @param {string} args.name - The name of the template to delete.
 * @returns {Promise<Object>} - The result of the deletion operation.
 */
const executeFunction = async ({ hsm_id, name }) => {
  const baseUrl = 'https://graph.facebook.com';
  const version = ''; // will be provided by the user
  const wabaId = ''; // will be provided by the user
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;

  try {
    // Construct the URL for the DELETE request
    const url = new URL(`${baseUrl}/${version}/${wabaId}/message_templates`);
    url.searchParams.append('hsm_id', hsm_id);
    url.searchParams.append('name', name);

    // Set up headers for the request
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    // Perform the fetch request
    const response = await fetch(url.toString(), {
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
 * Tool configuration for deleting a message template on WhatsApp Cloud API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'delete_template_by_id',
      description: 'Delete a message template by its ID on WhatsApp Cloud API.',
      parameters: {
        type: 'object',
        properties: {
          hsm_id: {
            type: 'string',
            description: 'The ID of the template to delete.'
          },
          name: {
            type: 'string',
            description: 'The name of the template to delete.'
          }
        },
        required: ['hsm_id', 'name']
      }
    }
  }
};

export { apiTool };