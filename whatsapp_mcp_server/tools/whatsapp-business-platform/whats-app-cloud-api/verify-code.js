/**
 * Function to verify a code sent via SMS or Voice for WhatsApp Cloud API.
 *
 * @param {Object} args - Arguments for the verification.
 * @param {string} args.code - The code received after requesting verification.
 * @param {string} args.phoneNumberId - The ID of the phone number associated with the WhatsApp Business Account.
 * @param {string} args.version - The version of the WhatsApp API to use.
 * @returns {Promise<Object>} - The result of the verification request.
 */
const executeFunction = async ({ code, phoneNumberId, version }) => {
  const baseUrl = 'https://graph.facebook.com';
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  try {
    // Construct the URL for the verification request
    const url = `${baseUrl}/${version}/${phoneNumberId}/verify_code`;

    // Set up headers for the request
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };

    // Prepare the body of the request
    const body = JSON.stringify({ code });

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
    console.error('Error verifying code:', error);
    return { error: 'An error occurred while verifying the code.' };
  }
};

/**
 * Tool configuration for verifying a code in WhatsApp Cloud API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'verify_code',
      description: 'Verify a code sent via SMS or Voice for WhatsApp Cloud API.',
      parameters: {
        type: 'object',
        properties: {
          code: {
            type: 'string',
            description: 'The code received after requesting verification.'
          },
          phoneNumberId: {
            type: 'string',
            description: 'The ID of the phone number associated with the WhatsApp Business Account.'
          },
          version: {
            type: 'string',
            description: 'The version of the WhatsApp API to use.'
          }
        },
        required: ['code', 'phoneNumberId', 'version']
      }
    }
  }
};

export { apiTool };