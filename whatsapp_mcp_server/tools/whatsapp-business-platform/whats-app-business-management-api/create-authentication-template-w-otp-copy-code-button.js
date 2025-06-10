/**
 * Function to create an authentication template with an OTP copy code button on WhatsApp.
 *
 * @param {Object} args - Arguments for creating the authentication template.
 * @param {string} args.name - The name of the authentication template.
 * @param {string} args.language - The language for the template.
 * @param {string} args.category - The category of the template.
 * @param {number} args.code_expiration_minutes - The expiration time for the code in minutes.
 * @returns {Promise<Object>} - The result of the template creation.
 */
const executeFunction = async ({ name, language = 'en_US', category = 'AUTHENTICATION', code_expiration_minutes = 10 }) => {
  const accessToken = ''; // will be provided by the user
  const apiVersion = ''; // will be provided by the user
  const wabaId = ''; // will be provided by the user
  const url = `https://graph.facebook.com/${apiVersion}/${wabaId}/message_templates`;

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
        'Authorization': `Bearer ${accessToken}`,
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
 * Tool configuration for creating an authentication template on WhatsApp.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'create_authentication_template',
      description: 'Create an authentication template with an OTP copy code button on WhatsApp.',
      parameters: {
        type: 'object',
        properties: {
          name: {
            type: 'string',
            description: 'The name of the authentication template.'
          },
          language: {
            type: 'string',
            description: 'The language for the template.'
          },
          category: {
            type: 'string',
            description: 'The category of the template.'
          },
          code_expiration_minutes: {
            type: 'integer',
            description: 'The expiration time for the code in minutes.'
          }
        },
        required: ['name']
      }
    }
  }
};

export { apiTool };