/**
 * Function to get the display name status for a specific phone number using WhatsApp Cloud API.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.version - The API version to use.
 * @param {string} args.phoneNumberId - The ID of the phone number to check the display name status for.
 * @returns {Promise<Object>} - The response containing the display name status.
 */
const executeFunction = async ({ version, phoneNumberId }) => {
  const baseUrl = 'https://graph.facebook.com';
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  try {
    // Construct the URL with query parameters
    const url = new URL(`${baseUrl}/${version}/${phoneNumberId}`);
    url.searchParams.append('fields', 'name_status');

    // Set up headers for the request
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    // Perform the fetch request
    const response = await fetch(url.toString(), {
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
 * Tool configuration for getting display name status using WhatsApp Cloud API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_display_name_status',
      description: 'Get the display name status for a specific phone number.',
      parameters: {
        type: 'object',
        properties: {
          version: {
            type: 'string',
            description: 'The API version to use.'
          },
          phoneNumberId: {
            type: 'string',
            description: 'The ID of the phone number to check the display name status for.'
          }
        },
        required: ['version', 'phoneNumberId']
      }
    }
  }
};

export { apiTool };