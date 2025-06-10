/**
 * Function to get phone numbers associated with a WhatsApp Business Account.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.WABA_ID - The ID of the WhatsApp Business Account.
 * @param {string} args.Version - The version of the API to use.
 * @returns {Promise<Object>} - The response containing phone numbers and their details.
 */
const executeFunction = async ({ WABA_ID, Version }) => {
  const baseUrl = 'https://graph.facebook.com';
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;

  try {
    // Construct the URL for the API request
    const url = `${baseUrl}/${Version}/${WABA_ID}/phone_numbers`;

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
    console.error('Error getting phone numbers:', error);
    return { error: 'An error occurred while getting phone numbers.' };
  }
};

/**
 * Tool configuration for getting phone numbers from WhatsApp Business Account.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_phone_numbers',
      description: 'Get phone numbers associated with a WhatsApp Business Account.',
      parameters: {
        type: 'object',
        properties: {
          WABA_ID: {
            type: 'string',
            description: 'The ID of the WhatsApp Business Account.'
          },
          Version: {
            type: 'string',
            description: 'The version of the API to use.'
          }
        },
        required: ['WABA_ID', 'Version']
      }
    }
  }
};

export { apiTool };