# botocore-libfaketime

This patches [botocore](https://github.com/boto/botocore) to work while [libfaketime](https://github.com/wolfcw/libfaketime) is being used to modify the system time. This only works when using relative offsets in libfaketime.

## Problem

The botocore package signs AWS requests using the current time. AWS uses this time stamp to protect against replay attacks and denies all requests that are not within 5 minutes of the real time. When libfaketime is configured to modify the time by more than 5 minutes, all requests made to AWS are denied and all AWS functionality is broken.

## Solution

This package monkey-patches botocore to effectively "undo" the time modification performed by libfaketime. It reads the libfaketime environment variables to determine the relative offset that libfaketime is using, and then subtracts that offset from timestamps used in requests.

### botocore:

Here is what happens when botocore is used without libfaketime.

1. botocore asks for the current time
1. the system returns the real time
1. botocore signs the request with the real time
1. AWS accepts the request

### botocore + libfaketime:

Here is what happens when botocore is used while libfaketime is configured to modify the time by more than 5 minutes.

1. botocore asks for the current time
1. libfaketime returns the modified time
1. botocore signs the request with the modified time
1. AWS denies the request

### botocore + libfaketime + botocore-libfaketime:

Here is what happens when botocore-libfaketime is used to solve the problem.

1. botocore asks for the current time
1. libfaketime returns the modified time
1. botocore-libfaketime modifies the modified time back to the real time
1. botocore signs the request with the real time
1. AWS accepts the request

## Usage

### Patch botocore using an import statement:

```python
import botocore_libfaketime.patch
```

### Patch botocore using a function call:

```python
import botocore_libfaketime

botocore_libfaketime.patch_botocore()
```
