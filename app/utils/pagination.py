def with_pagination(collection, query={}, args={}, order_sorted=None, field_sorted=None):
    """
        :param collection: Model
        :param query: filtro a ser aplicado
        :param args: esperado um dicionario com current e pageSize
        :param order_sorted: DESC ou ASC
        :param field_sorted: campo a ser ordenado
        :return: lista com paginação
        """
    offset = 1
    limit = 100
    if args.get('current') and args.get('page_size'):
        offset = int(args['current'])
        limit = int(args['page_size'])
    skips = limit * (offset - 1)
    res = {"pagination": {}}
    documents = collection.objects(__raw__=query)
    total = len(documents)
    if field_sorted and order_sorted:
        short = {'DESC': '-', 'ASC': '+'}
        order_by = f"{short[order_sorted]}{field_sorted}"
        documents = documents.order_by(order_by)
    data = documents.skip(skips).limit(limit)
    data = [item.as_dict() for item in data]
    max_page = int(total / limit) if total % limit == 0 else int(total / limit) + 1
    res["pagination"]["total"] = total
    res["pagination"]["max_page"] = max_page
    res["pagination"]["page_size"] = limit
    res["pagination"]["current"] = offset
    res["data"] = data
    return res