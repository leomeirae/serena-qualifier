/**
 * Function to get analytics from the WhatsApp Business Management API.
 *
 * @param {Object} args - Arguments for the analytics request.
 * @param {string} args.apiVersion - The API version to use.
 * @param {string} args.wabaId - The WhatsApp Business Account ID.
 * @param {number} args.start - The start timestamp for analytics.
 * @param {number} args.end - The end timestamp for analytics.
 * @param {Array<string>} [args.phoneNumbers=[]] - An array of phone numbers to include in the request.
 * @param {Array<string>} [args.countryCodes=["US", "BR"]] - An array of country codes to include in the request.
 * @returns {Promise<Object>} - The result of the analytics request.
 */
const executeFunction = async ({ apiVersion, wabaId, start, end, phoneNumbers = [], countryCodes = ["US", "BR"] }) => {
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const baseUrl = 'https://graph.facebook.com';
  
  try {
    // Construct the URL with query parameters
    const url = new URL(`${baseUrl}/${apiVersion}/${wabaId}`);
    url.searchParams.append('fields', `analytics.start(${start}).end(${end}).granularity(DAY).phone_numbers(${JSON.stringify(phoneNumbers)}).country_codes(${JSON.stringify(countryCodes)})`);

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
    console.error('Error getting analytics:', error);
    return { error: 'An error occurred while getting analytics.' };
  }
};

/**
 * Tool configuration for getting analytics from the WhatsApp Business Management API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_analytics',
      description: 'Get analytics from the WhatsApp Business Management API.',
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
          },
          start: {
            type: 'integer',
            description: 'The start timestamp for analytics.'
          },
          end: {
            type: 'integer',
            description: 'The end timestamp for analytics.'
          },
          phoneNumbers: {
            type: 'array',
            items: {
              type: 'string'
            },
            description: 'An array of phone numbers to include in the request.'
          },
          countryCodes: {
            type: 'array',
            items: {
              type: 'string'
            },
            description: 'An array of country codes to include in the request.'
          }
        },
        required: ['apiVersion', 'wabaId', 'start', 'end']
      }
    }
  }
};

export { apiTool };