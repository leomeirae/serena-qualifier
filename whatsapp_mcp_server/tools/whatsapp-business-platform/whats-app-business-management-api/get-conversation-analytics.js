/**
 * Function to get conversation analytics from the WhatsApp Business Management API.
 *
 * @param {Object} args - Arguments for the request.
 * @param {string} args.apiVersion - The API version to use.
 * @param {string} args.wabaId - The WhatsApp Business Account ID.
 * @param {number} args.start - The start timestamp for the analytics.
 * @param {number} args.end - The end timestamp for the analytics.
 * @returns {Promise<Object>} - The conversation analytics data.
 */
const executeFunction = async ({ apiVersion, wabaId, start, end }) => {
  const token = process.env.WHATSAPP_BUSINESS_PLATFORM_API_KEY;
  const baseUrl = `https://graph.facebook.com/${apiVersion}/${wabaId}`;
  const fields = `conversation_analytics.start(${start}).end(${end}).granularity(MONTHLY).conversation_directions(["business_initiated"]).dimensions(["conversation_type", "conversation_direction"])`;

  try {
    // Set up headers for the request
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    // Perform the fetch request
    const response = await fetch(`${baseUrl}?fields=${encodeURIComponent(fields)}`, {
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
    console.error('Error getting conversation analytics:', error);
    return { error: 'An error occurred while getting conversation analytics.' };
  }
};

/**
 * Tool configuration for getting conversation analytics from the WhatsApp Business Management API.
 * @type {Object}
 */
const apiTool = {
  function: executeFunction,
  definition: {
    type: 'function',
    function: {
      name: 'get_conversation_analytics',
      description: 'Get conversation analytics from the WhatsApp Business Management API.',
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
            description: 'The start timestamp for the analytics.'
          },
          end: {
            type: 'integer',
            description: 'The end timestamp for the analytics.'
          }
        },
        required: ['apiVersion', 'wabaId', 'start', 'end']
      }
    }
  }
};

export { apiTool };