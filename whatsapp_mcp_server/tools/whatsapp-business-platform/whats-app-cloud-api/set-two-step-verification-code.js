/**
 * Function to set the two-step verification code for a WhatsApp account.
 *
 * @param {Object} args - Arguments for setting the two-step verification code.
 * @param {string} args.pin - A 6-digit PIN to use for two-step verification.
 * @param {string} args.version - The API version to use for the request.
 * @param {string} args.phoneNumberId - The phone number ID associated with the WhatsApp account.
 * @returns {Promise<Object>} - The result of the two-step verification code setting operation.
 */
const executeFunction = async ({ pin, version, phoneNumberId }) => {
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const url = `https://graph.facebook.com/${version}/${phoneNumberId}`;
  
  try {
    // Set up headers for the request
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    // Prepare the request body
    const body = JSON.stringify({ pin });

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
    console.error('Error setting two-step verification code:', error);
    return { error: 'An error occurred while setting the two-step verification code.' };
  }
};

/**
 * Tool configuration for setting two-step verification code on WhatsApp.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'set_two_step_verification_code',
      description: 'Set the two-step verification code for a WhatsApp account.',
      parameters: {
        type: 'object',
        properties: {
          pin: {
            type: 'string',
            description: 'A 6-digit PIN to use for two-step verification.'
          },
          version: {
            type: 'string',
            description: 'The API version to use for the request.'
          },
          phoneNumberId: {
            type: 'string',
            description: 'The phone number ID associated with the WhatsApp account.'
          }
        },
        required: ['pin', 'version', 'phoneNumberId']
      }
    }
  }
};

export { apiTool };