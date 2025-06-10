/**
 * Function to get the display name status of a business phone number using the WhatsApp Business Management API.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.apiVersion - The API version to use for the request.
 * @param {string} args.businessPhoneNumberId - The ID of the business phone number.
 * @returns {Promise<Object>} - The response containing the display phone number and name status.
 */
const executeFunction = async ({ apiVersion, businessPhoneNumberId }) => {
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const baseUrl = 'https://graph.facebook.com';
  
  try {
    // Construct the URL for the request
    const url = `${baseUrl}/${apiVersion}/${businessPhoneNumberId}?fields=id,display_phone_number,name_status`;

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
    console.error('Error getting display name status:', error);
    return { error: 'An error occurred while getting the display name status.' };
  }
};

/**
 * Tool configuration for getting the display name status of a business phone number.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_business_phone_number_display_name_status',
      description: 'Get the display name status of a business phone number.',
      parameters: {
        type: 'object',
        properties: {
          apiVersion: {
            type: 'string',
            description: 'The API version to use for the request.'
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