/**
 * Function to get the business phone number from the WhatsApp Business Management API.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.apiVersion - The API version to use.
 * @param {string} args.businessPhoneNumberId - The ID of the business phone number.
 * @returns {Promise<Object>} - The response from the API containing the business phone number details.
 */
const executeFunction = async ({ apiVersion, businessPhoneNumberId }) => {
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const url = `https://graph.facebook.com/${apiVersion}/${businessPhoneNumberId}`;
  
  try {
    // Set up headers for the request
    const headers = {
      'Authorization': `Bearer ${token}`
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
    console.error('Error retrieving business phone number:', error);
    return { error: 'An error occurred while retrieving the business phone number.' };
  }
};

/**
 * Tool configuration for getting the business phone number from the WhatsApp Business Management API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_business_phone_number',
      description: 'Retrieve the business phone number details from the WhatsApp Business Management API.',
      parameters: {
        type: 'object',
        properties: {
          apiVersion: {
            type: 'string',
            description: 'The API version to use.'
          },
          businessPhoneNumberId: {
            type: 'string',
            description: 'The ID of the business phone number.'
          }
        },
        required: ['apiVersion', 'businessPhoneNumberId']
      }
    }
  }
};

export { apiTool };