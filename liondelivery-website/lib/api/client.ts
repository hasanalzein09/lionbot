import { API_BASE_URL } from "@/lib/utils/constants";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface FetchOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
}

export async function apiClient<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { params, ...fetchOptions } = options;

  // Build URL with query params
  let url = `${API_BASE_URL}${endpoint}`;
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== "") {
        searchParams.append(key, String(value));
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  const response = await fetch(url, {
    ...fetchOptions,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...fetchOptions.headers,
    },
  });

  // Handle non-JSON responses
  const contentType = response.headers.get("content-type");
  if (!contentType?.includes("application/json")) {
    if (!response.ok) {
      throw new ApiError(
        `HTTP Error: ${response.status}`,
        response.status
      );
    }
    return {} as T;
  }

  const data = await response.json();

  if (!response.ok) {
    throw new ApiError(
      data.message || data.error || `HTTP Error: ${response.status}`,
      response.status,
      data
    );
  }

  return data as T;
}

// Helper for GET requests
export function get<T>(endpoint: string, params?: Record<string, string | number | boolean | undefined>) {
  return apiClient<T>(endpoint, { method: "GET", params });
}

// Helper for POST requests
export function post<T>(endpoint: string, body?: unknown) {
  return apiClient<T>(endpoint, {
    method: "POST",
    body: body ? JSON.stringify(body) : undefined,
  });
}

// Helper for PUT requests
export function put<T>(endpoint: string, body?: unknown) {
  return apiClient<T>(endpoint, {
    method: "PUT",
    body: body ? JSON.stringify(body) : undefined,
  });
}

// Helper for DELETE requests
export function del<T>(endpoint: string) {
  return apiClient<T>(endpoint, { method: "DELETE" });
}
