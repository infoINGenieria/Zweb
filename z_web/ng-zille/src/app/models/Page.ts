export class Page {
    // The number of elements in the page
    size = 0;
    // The total number of elements
    totalElements = 0;
    // The total number of pages
    totalPages = 0;
    // The current page number
    pageNumber = 1;
}

/**
 * An array of data with an associated page object used for paging
 */
export class PagedData<T> {
    data = new Array<T>();
    page = new Page();
}
