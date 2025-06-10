/**
 * Function to request a verification code for a phone number using WhatsApp Cloud API.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.phoneNumberId - The ID of the phone number to verify.
 * @param {string} [args.codeMethod="SMS"] - The method for verification, either "SMS" or "VOICE".
 * @param {string} [args.locale="en_US"] - The locale for the request.
 * @returns {Promise<Object>} - The result of the verification code request.
 */
const executeFunction = async ({ phoneNumberId, codeMethod = 'SMS', locale = 'en_US' }) => {
  const baseUrl = 'https://graph.facebook.com';
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const version = ''; // will be provided by the user

  try {
    const url = `${baseUrl}/${version}/${phoneNumberId}/request_code`;

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };

    const body = JSON.stringify({
      code_method: codeMethod,
      locale: locale
    });

    const response = await fetch(url, {
      method: 'POST',
      headers: headers,
      body: body
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error requesting verification code:', error);
    return { error: 'An error occurred while requesting the verification code.' };
  }
};

/**
 * Tool configuration for requesting a verification code for a phone number using WhatsApp Cloud API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'request_verification_code',
      description: 'Request a verification code for a phone number using WhatsApp Cloud API.',
      parameters: {
        type: 'object',
        properties: {
          phoneNumberId: {
            type: 'string',
            description: 'The ID of the phone number to verify.'
          },
          codeMethod: {
            type: 'string',
            enum: ['SMS', 'VOICE'],
            description: 'The method for verification, either "SMS" or "VOICE".'
          },
          locale: {
            type: 'string',
            description: 'The locale for the request.'
          }
        },
        required: ['phoneNumberId']
      }
    }
  }
};

export { apiTool };