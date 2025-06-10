/**
 * Function to create an authentication template with an OTP copy code button using the WhatsApp Cloud API.
 *
 * @param {Object} args - Arguments for creating the authentication template.
 * @param {string} args.name - The name of the authentication template.
 * @param {string} args.language - The language code for the template.
 * @param {string} args.category - The category of the template.
 * @param {number} args.code_expiration_minutes - The expiration time for the OTP code in minutes.
 * @returns {Promise<Object>} - The result of the template creation.
 */
const executeFunction = async ({ name, language, category, code_expiration_minutes }) => {
  const version = ''; // will be provided by the user
  const wabaId = ''; // will be provided by the user
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;

  const url = `https://graph.facebook.com/${version}/${wabaId}/message_templates`;
  
  const body = {
    name,
    language,
    category,
    components: [
      {
        type: "BODY",
        add_security_recommendation: true
      },
      {
        type: "FOOTER",
        code_expiration_minutes
      },
      {
        type: "BUTTONS",
        buttons: [
          {
            type: "OTP",
            otp_type: "COPY_CODE",
            text: "Copy Code"
          }
        ]
      }
    ]
  };

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error creating authentication template:', error);
    return { error: 'An error occurred while creating the authentication template.' };
  }
};

/**
 * Tool configuration for creating an authentication template with OTP button on WhatsApp Cloud API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'create_auth_template',
      description: 'Create an authentication template with an OTP copy code button.',
      parameters: {
        type: 'object',
        properties: {
          name: {
            type: 'string',
            description: 'The name of the authentication template.'
          },
          language: {
            type: 'string',
            description: 'The language code for the template.'
          },
          category: {
            type: 'string',
            description: 'The category of the template.'
          },
          code_expiration_minutes: {
            type: 'integer',
            description: 'The expiration time for the OTP code in minutes.'
          }
        },
        required: ['name', 'language', 'category', 'code_expiration_minutes']
      }
    }
  }
};

export { apiTool };