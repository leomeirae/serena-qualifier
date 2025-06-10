/**
 * Function to get all business phone numbers associated with a WhatsApp Business Account.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.apiVersion - The API version to use.
 * @param {string} args.wabaId - The WhatsApp Business Account ID.
 * @returns {Promise<Object>} - The response containing the list of phone numbers.
 */
const executeFunction = async ({ apiVersion, wabaId }) => {
  const baseUrl = 'https://graph.facebook.com';
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  try {
    // Construct the URL for the API request
    const url = `${baseUrl}/${apiVersion}/${wabaId}/phone_numbers`;

    // Set up headers for the request
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    // Perform the fetch request
    const response = await fetch(url, {
      method: 'GET',
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
    console.error('Error retrieving business phone numbers:', error);
    return { error: 'An error occurred while retrieving business phone numbers.' };
  }
};

/**
 * Tool configuration for getting business phone numbers from WhatsApp Business Management API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_business_phone_numbers',
      description: 'Retrieve all business phone numbers associated with a WhatsApp Business Account.',
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
          }
        },
        required: ['apiVersion', 'wabaId']
      }
    }
  }
};

export { apiTool };