#!/usr/bin/env perl

use v5.40;
use utf8;
use warnings;

use Data::Dumper;
use XML::Parser;

package main;

my $out = \*STDOUT;

sub extract_response {
    my ($raw) = @_;
    $raw =~ s/\"$//;
    my @res = split /\n/, $raw;
    @res = splice @res, 3;
    join "\n", @res;
}

my $cmd = 'dbus-send --system \
  --dest=org.jfhbrook.plusdeck "/" \
  --print-reply \
  org.freedesktop.DBus.Introspectable.Introspect';

my $raw = `$cmd`;
my $res = &extract_response($raw);

my $parser = XML::Parser->new( Style => 'Tree' );
my $bus    = $parser->parse($res);

my $iface_name = 'org.jfhbrook.plusdeck';

&process_bus( @{ $bus->[1] } );

sub process_bus {
    while (@_) {
        my $child = shift;
        if ( $child eq 'interface' ) {
            my $iface = shift;
            &process_iface( @{$iface} );
        }
    }
}

sub process_iface {
    my %props = %{ shift @_ };

    if ( $props{'name'} eq $iface_name ) {
        print $out "## $props{'name'}\n\n";
        while (@_) {
            my $child = shift;
            if ( $child eq 0 ) {
                shift;
                next;
            }
            elsif ( $child eq 'method' ) {
                &process_method( @{ shift @_ } );
            }
            elsif ( $child eq 'property' ) {
                &process_property( @{ shift @_ } );
            }
            elsif ( $child eq 'signal' ) {
                &process_signal( @{ shift @_ } );
            }
            else {
                print $out Dumper($child);
            }
        }
    }
}

sub process_method {
    my %props = %{ shift @_ };
    print $out "### Method: $props{'name'}\n\n";
    my @args;
    my $ret = 'void';
    my @anns;

    while (@_) {
        my $child = shift;
        if ( $child eq 0 ) {
            shift;
            next;
        }
        elsif ( $child eq 'arg' ) {
            my @children = @{ shift @_ };
            my %props    = %{ $children[0] };
            if ( $props{'direction'} eq 'in' ) {
                push( @args, $props{'type'} );
            }
            elsif ( $props{'direction'} eq 'out' ) {
                $ret = $props{'type'};
            }
            else {
                print $out Dumper(%props);
            }
        }
        elsif ( $child eq 'annotation' ) {
            my $ann = &process_annotation( @{ shift @_ } );
            push @anns, $ann;
        }
        else {
            print $out Dumper($child);
        }
    }

    print_annotations(@anns);

    if (@args) {
        print $out '**Arguments:** ';
        print $out join( ", ", @args ) . "\n";
    }
    print $out "**Returns: $ret\n\n";
}

sub process_property {
    my %props = %{ shift @_ };
    print $out "### Property: $props{'name'}\n\n";
    my @anns;

    while (@_) {
        my $child = shift;
        if ( $child eq 0 ) {
            shift;
            next;
        }
        elsif ( $child eq 'annotation' ) {
            my $ann = &process_annotation( @{ shift @_ } );
            push @anns, $ann;
        }
        else {
            print $out Dumper($child);
        }
    }

    print_annotations(@anns);
}

sub process_signal {
    my %props = %{ shift @_ };
    print $out "### Signal: $props{'name'}\n\n";
    my $type = 'void';
    my @anns;

    while (@_) {
        my $child = shift;
        if ( $child eq 0 ) {
            shift;
            next;
        }
        elsif ( $child eq 'arg' ) {
            my @children = @{ shift @_ };
            my %props    = %{ $children[0] };
            $type = $props{'type'};
        }
        elsif ( $child eq 'annotation' ) {
            my $ann = &process_annotation( @{ shift @_ } );
            push @anns, $ann;
        }
        else {
            print $out Dumper($child);
        }
    }

    print_annotations(@anns);
    print $out "**Type: $type\n\n";
}

sub process_annotation {
    my %props = %{ shift @_ };
    "- $props{'name'}: $props{'value'}";
}

sub print_annotations {
    if ( !@_ ) {
        return;
    }

    print $out "**Annotations:**\n\n";
    foreach (@_) {
        print $out "$_\n";
    }
    print $out "\n";
}
