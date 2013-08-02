jones
=====
[![travis][2]][1]

Jones is a configuration frontend for Zookeeper.

Goals
-----

   * Clients MUST only talk to zookeeper
   * Accessing configuration MUST be simple (i.e. no computation)
   * Unique views of the config must be available on a host-by-host basis

Introduction
------------

At their root, most configuration systems are a hierarchy of dictionaries. The root has config common to all environments,
with config specific to say, developers or a staging area, inheriting and overriding values. Jones takes this idea and
maps it to Zookeeper.

Zookeeper is the ideal place for configuration. Besides its availability guarantees, it's also able to update observers
when data changes. Now we can change config at runtime, making possible a whole category of use-cases like switches, a/b
tests, and knob and lever you can imagine.

Using the client
----------------

Jones comes with an example client, which we hope will serve the most general case.
It's also incredibly simple (only 30 lines), so it should be easy to customize. Using it is just as straight-forward.

**Install:**

    pip install jones

**Use:**

    from jones.client import JonesClient

    # Initialize jones client with kazoo connection, and service.
    jones = JonesClient(zk, 'da')
    client['key']
    'value'
    client.get('missingkey', 'default')
    'default'


- zk
    - An instance of `kazoo.client.KazooClient`.
- service
    - The name of the service you want config for.

The JonesClient object also takes an optional callback and association.
- cb
    - A method to be called with a config dict every time it changes.
- association
    - A key in the _associations_ map. By default JonesClient uses `socket.getfqdn()`.


Design
------

Environments are stored under their parent znodes on the zookeeper data tree. On write, the view algorithm is used to
materialize the "inherited" config in a view node.

Jones takes advantage of zookeeper's mvcc capabilities where possible. An environment will never have its data clobbered
by a concurrent write. When updating a view, however, the last write wins. This may cause view data to be clobbered if
concurrent writes are made to two nodes in the same path and Jones happens to lose its session in between (see issue #1).

Associations are a simple key to env map, stored under /nodemaps.

Example data tree dump. This shows data for an example service:

```
/services
  /testservice
    /conf
      foo = u'bar'
      /parent
        a = 1
        b = [1, 2, 3]
        c = {u'x': 0}
        /child1
          a = 2
    /nodemaps
      127.0.0.1 -> /services/testservice/views/parent
      127.0.0.2 -> /services/testservice/views/parent/child1
    /views
      foo = u'bar'
      /parent
        a = 1
        b = [1, 2, 3]
        c = {u'x': 0}
        foo = u'bar'
        /child1
          a = 2
          b = [1, 2, 3]
          c = {u'x': 0}
          foo = u'bar'
```

Glossary
--------


- Config Tree
    - The hierarchy of nodes.
- Node
    - A node in the config tree. Nodes hold configuration for an environment. Implemented as a znode.
- Environment
  <dd>Also seen as <em>env</em> in the code, an environment is the path to a specific node in the config tree
  (i.e. parent/child).</dd>
- Association
    - The identifier a client will use to address a node. Any string will work, but the fqdn or ip address are common.
- View
  <dd>A view is a node which has has the following algorithm applied
    <pre>for node in root -> env
  update view with node.config</pre>
  </dd>


Screenshot
----------
![Example](http://mwhooker.github.com/jones/docs/img/testservice.png)

  [1]: https://travis-ci.org/mwhooker/jones
  [2]: https://travis-ci.org/mwhooker/jones.png?branch=master
