export const formatKey = (key) => {
  if (!key) return "";
  // Split by underscore or hyphen
  const words = key.split(/_|-/);
  // Capitalize first letter of each word
  return words
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

export const formatValue = (value) => {
  if (typeof value === "number") {
    // Check if it's a float
    if (value % 1 !== 0) {
      return value.toFixed(3);
    }
    return value;
  }
  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }
  if (value === null || value === undefined) {
    return "N/A";
  }
  return value.toString();
};
