# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import aws_cdk as cdk

from .configuration import (
    get_logical_id_prefix, get_resource_name_prefix,
)


COST_CENTER = 'COST_CENTER'
TAG_ENVIRONMENT = 'TAG_ENVIRONMENT'
TEAM = 'TEAM'
APPLICATION = 'APPLICATION'


def tag(stack, target_environment: str):
    """
    Adds a tag to all constructs in the stack

    @param stack: The stack to tag
    @param target_environment: The environment the stack is deployed to
    """
    cdk.Tags.of(stack).add(*get_tag(COST_CENTER, target_environment))
    cdk.Tags.of(stack).add(*get_tag(TAG_ENVIRONMENT, target_environment))
    cdk.Tags.of(stack).add(*get_tag(TEAM, target_environment))
    cdk.Tags.of(stack).add(*get_tag(APPLICATION, target_environment))


def get_tag(tag_name, target_environment) -> dict:
    """
    Get a tag for a given parameter and target environment.

    @param tag_name: The name of the tag
    @param target_environment: The environment the tag is applied to
    """
    logical_id_prefix = get_logical_id_prefix()
    resource_name_prefix = get_resource_name_prefix()
    tag_map = {
        COST_CENTER: [
            f'{resource_name_prefix}:cost-center',
            f'{logical_id_prefix}Infrastructure',
        ],
        TAG_ENVIRONMENT: [
            f'{resource_name_prefix}:environment',
            target_environment,
        ],
        TEAM: [
            f'{resource_name_prefix}:team',
            f'{logical_id_prefix}Admin',
        ],
        APPLICATION: [
            f'{resource_name_prefix}:application',
            f'{logical_id_prefix}Infrastructure',
        ],
    }
    if tag_name not in tag_map:
        raise AttributeError(f'Tag map does not contain a key/value for {tag_name}')

    return tag_map[tag_name]
